<?php
/* Copyright (C) 2026        Jessica Kowal            <jessicakowal69@gmail.com>
 * Copyright (C) 2026        Charlene Benke           <charlene@patas-monkey.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

use Luracast\Restler\RestException;

dol_include_once('/timekeepr/class/timeplanned.class.php');
require_once DOL_DOCUMENT_ROOT .'/core/class/timespent.class.php';

/**
 * API class for Time Planned and Time Spent
 *
 * @access protected
 * @class  DolibarrApiAccess {@requires user,external}
 */
class Timekeeprapi extends DolibarrApi
{
    /**
     * @var TimePlanned $timeplanned {@type TimePlanned}
     */
    public $timeplanned;

    /**
     * @var TimeSpent $timespent {@type TimeSpent}
     */
    public $timespent;

    public $db;

    /**
     * @var array   $FIELDS     Mandatory fields for TimePlanned
     */
    static $FIELDS = array(
        'fk_element',
        'elementtype',
        'element_duration'
    );

    /**
     * @var array   $FIELDS_SPENT     Mandatory fields for TimeSpent
     */
    static $FIELDS_SPENT = array(
        'fk_element',
        'elementtype',
        'element_duration',
        'fk_user',
        'element_date'
    );

    /**
     * Constructor
     */
    public function __construct()
    {
        global $db;
        $this->db = $db;
        $this->timeplanned = new TimePlanned($this->db);
        $this->timespent = new TimeSpent($this->db);
    }

    /**
     * Get properties of a time planned object
     *
     * @param   int     $id     ID of time planned
     * @return  array|mixed     Data without useless information
     *
     * @throws  RestException
     *
     * @url GET /planned/{id}
     */
    public function planned_get($id)
    {
        if (!DolibarrApiAccess::$user->hasRight('timekeepr', 'read')) {
            throw new RestException(403, "Access denied. Required right: timekeepr/read");
        }

        $result = $this->timeplanned->fetch($id);
        if (!$result) {
            throw new RestException(404, 'Time planned not found');
        }

        if (!DolibarrApi::_checkAccessToResource('timeplanned', $this->timeplanned->id)) {
            throw new RestException(403, 'Access not allowed for login ' . DolibarrApiAccess::$user->login);
        }

        return $this->_cleanObjectDatas($this->timeplanned);
    }

    /**
     * List time planned records
     *
     * @param string      $sortfield     Sort field
     * @param string      $sortorder     Sort order
     * @param int         $limit         Limit for list
     * @param int         $page          Page number
     * @param string      $sqlfilters    Other criteria to filter answers separated by a comma
     * @param string      $properties    Restrict the data returned to these properties
     * @return array                     Array of time planned objects
     *
     * @url GET /planned
     */
    public function planned_index($sortfield = "t.rowid", $sortorder = 'ASC', $limit = 100, $page = 0, $sqlfilters = '', $properties = '')
    {
        if (!DolibarrApiAccess::$user->hasRight('timekeepr', 'read')) {
            throw new RestException(403, "Access denied. Required right: timekeepr/read");
        }

        $obj_ret = array();

        $sql = "SELECT t.rowid";
        $sql .= " FROM " . MAIN_DB_PREFIX . "element_time_planned AS t";
        $sql .= " WHERE 1 = 1";

        // Add sql filters
        if ($sqlfilters) {
            $errormessage = '';
            $sql .= forgeSQLFromUniversalSearchCriteria($sqlfilters, $errormessage);
            if ($errormessage) {
                throw new RestException(400, 'Error when validating parameter sqlfilters -> ' . $errormessage);
            }
        }

        $sql .= $this->db->order($sortfield, $sortorder);
        if ($limit) {
            if ($page < 0) {
                $page = 0;
            }
            $offset = $limit * $page;
            $sql .= $this->db->plimit($limit + 1, $offset);
        }

        $result = $this->db->query($sql);

        if ($result) {
            $num = $this->db->num_rows($result);
            $min = min($num, ($limit <= 0 ? $num : $limit));
            $i = 0;
            while ($i < $min) {
                $obj = $this->db->fetch_object($result);
                $timeplanned_static = new \TimePlanned($this->db);
                if ($timeplanned_static->fetch($obj->rowid)) {
                    $obj_ret[] = $this->_filterObjectProperties($this->_cleanObjectDatas($timeplanned_static), $properties);
                }
                $i++;
            }
        } else {
            throw new RestException(503, 'Error when retrieve time planned list : ' . $this->db->lasterror());
        }

        return $obj_ret;
    }

    /**
     * Create time planned object
     *
     * @param   array   $request_data   Request data
     * @return  int     ID of created object
     *
     * @url POST /planned
     */
    public function planned_post($request_data = null)
    {
        if (!DolibarrApiAccess::$user->hasRight('timekeepr', 'saisir')) {
            throw new RestException(403, "Insufficient rights. Required: timekeepr/saisir");
        }

        // Check mandatory fields
        foreach (self::$FIELDS as $field) {
            if (!isset($request_data[$field])) {
                throw new RestException(400, "$field field missing");
            }
        }

        foreach ($request_data as $field => $value) {
            if ($field === 'caller') {
                $this->timeplanned->context['caller'] = sanitizeVal($request_data['caller'], 'aZ09');
                continue;
            }
            $this->timeplanned->$field = $this->_checkValForAPI($field, $value, $this->timeplanned);
        }

        // Required fields validation
        if (empty($this->timeplanned->fk_element) || empty($this->timeplanned->elementtype)) {
            throw new RestException(400, "fk_element and elementtype are mandatory");
        }

        if ($this->timeplanned->create(DolibarrApiAccess::$user) < 0) {
            throw new RestException(
                    500, "Error creating time planned", 
                    array_merge(array($this->timeplanned->error), $this->timeplanned->errors)
                );
        }

        return $this->timeplanned->id;
    }

    /**
     * Update time planned object
     *
     * @param   int     $id             ID of time planned to update
     * @param   array   $request_data   Data
     * @return  Object                  Updated object
     *
     * @url PUT /planned/{id}
     */
    public function planned_put($id, $request_data = null)
    {
        if (!DolibarrApiAccess::$user->hasRight('timekeepr', 'saisir')) {
            throw new RestException(403, "Insufficient rights. Required: timekeepr/saisir");
        }

        $result = $this->timeplanned->fetch($id);
        if (!$result) {
            throw new RestException(404, 'Time planned not found');
        }

        if (!DolibarrApi::_checkAccessToResource('timeplanned', $this->timeplanned->id)) {
            throw new RestException(403, 'Access not allowed for login ' . DolibarrApiAccess::$user->login);
        }

        foreach ($request_data as $field => $value) {
            if ($field == 'id') {
                continue;
            }
            if ($field === 'caller') {
                $this->timeplanned->context['caller'] = sanitizeVal($request_data['caller'], 'aZ09');
                continue;
            }
            $this->timeplanned->$field = $this->_checkValForAPI($field, $value, $this->timeplanned);
        }

        if ($this->timeplanned->update(DolibarrApiAccess::$user) > 0) {
            return $this->planned_get($id); // Correction: utiliser planned_get au lieu de get
        } else {
            throw new RestException(500, $this->timeplanned->error);
        }
    }

    /**
     * Delete time planned
     *
     * @param   int     $id     Time planned ID
     * @return  array
     *
     * @url DELETE /planned/{id}
     */
    public function planned_delete($id)
    {
        if (!DolibarrApiAccess::$user->hasRight('timekeepr', 'saisir')) {
            throw new RestException(403, "Insufficient rights. Required: timekeepr/saisir");
        }

        $result = $this->timeplanned->fetch($id);
        if (!$result) {
            throw new RestException(404, 'Time planned not found');
        }

        if (!DolibarrApi::_checkAccessToResource('timeplanned', $this->timeplanned->id)) {
            throw new RestException(403, 'Access not allowed for login ' . DolibarrApiAccess::$user->login);
        }

        if ($this->timeplanned->delete(DolibarrApiAccess::$user) <= 0) {
            throw new RestException(500, 'Error when delete time planned : ' . $this->timeplanned->error);
        }

        return array(
            'success' => array(
                'code' => 200,
                'message' => 'Time planned deleted'
            )
        );
    }

    /**
     * Get properties of a time spent object
     *
     * @param   int     $id     ID of time spent
     * @return  array|mixed     Data without useless information
     *
     * @throws  RestException
     *
     * @url GET /spent/{id}
     */
    public function spent_get($id)
    {
        if (!DolibarrApiAccess::$user->hasRight('timekeepr', 'read')) {
            throw new RestException(403, "Access denied. Required right: timekeepr/read");
        }

        // Utiliser une requête SQL directe pour récupérer tous les champs
        $sql = "SELECT * FROM " . MAIN_DB_PREFIX . "element_time";
        $sql .= " WHERE rowid = " . ((int) $id);

        $result = $this->db->query($sql);
        if (!$result) {
            throw new RestException(500, 'Error retrieving time spent: ' . $this->db->lasterror());
        }

        $obj = $this->db->fetch_object($result);
        if (!$obj) {
            throw new RestException(404, 'Time spent not found');
        }

        // Vérifier l'accès à la ressource
        if (!DolibarrApi::_checkAccessToResource('timespent', $obj->rowid)) {
            throw new RestException(403, 'Access not allowed for login ' . DolibarrApiAccess::$user->login);
        }

        // Créer un objet TimeSpent et le remplir avec les données
        $timespent = new TimeSpent($this->db);

        // Propriétés essentielles pour l'identification de l'objet
        $timespent->module = 'timespent';
        $timespent->element = 'timespent';
        $timespent->table_element = 'element_time';

        // Propriétés de l'enregistrement
        $timespent->id = $obj->rowid;
        $timespent->rowid = $obj->rowid;
        $timespent->fk_element = $obj->fk_element;
        $timespent->elementtype = $obj->elementtype;
        $timespent->element_date = $obj->element_date;
        $timespent->element_duration = $obj->element_duration;
        $timespent->fk_user = $obj->fk_user;
        $timespent->note = $obj->note;
        $timespent->fk_product = $obj->fk_product;
        $timespent->thm = $obj->thm;
        $timespent->invoice_id = $obj->invoice_id;
        $timespent->invoice_line_id = $obj->invoice_line_id;
        $timespent->intervention_id = $obj->intervention_id;
        $timespent->intervention_line_id = $obj->intervention_line_id;
        $timespent->datec = $obj->datec;
        $timespent->tms = $obj->tms;
        $timespent->ref_ext = $obj->ref_ext;
        $timespent->element_datehour = $obj->element_datehour;
        $timespent->element_date_withhour = $obj->element_date_withhour;
        $timespent->import_key = $obj->import_key;
        $timespent->ref = $obj->rowid; // Utiliser rowid comme ref

        return $this->_cleanObjectDatas($timespent);
    }


    /**
     * List time spent records
     *
     * @param string      $sortfield     Sort field
     * @param string      $sortorder     Sort order
     * @param int         $limit         Limit for list
     * @param int         $page          Page number
     * @param string      $sqlfilters    Other criteria to filter answers separated by a comma
     * @param string      $properties    Restrict the data returned to these properties
     * @return array                     Array of time spent objects
     *
     * @url GET /spent
     */
    public function spent_index($sortfield = "t.rowid", $sortorder = 'ASC', $limit = 100, $page = 0, $sqlfilters = '', $properties = '')
    {
        if (!DolibarrApiAccess::$user->hasRight('timekeepr', 'read')) {
            throw new RestException(403, "Access denied. Required right: timekeepr/read");
        }

        $obj_ret = array();

        $sql = "SELECT t.rowid";
        $sql .= " FROM " . MAIN_DB_PREFIX . "element_time AS t";
        $sql .= " WHERE 1 = 1";

        // Add sql filters
        if ($sqlfilters) {
            $errormessage = '';
            $sql .= forgeSQLFromUniversalSearchCriteria($sqlfilters, $errormessage);
            if ($errormessage) {
                throw new RestException(400, 'Error when validating parameter sqlfilters -> ' . $errormessage);
            }
        }

        $sql .= $this->db->order($sortfield, $sortorder);
        if ($limit) {
            if ($page < 0) {
                $page = 0;
            }
            $offset = $limit * $page;
            $sql .= $this->db->plimit($limit + 1, $offset);
        }

        $result = $this->db->query($sql);

        if ($result) {
            $num = $this->db->num_rows($result);
            $min = min($num, ($limit <= 0 ? $num : $limit));
            $i = 0;
            while ($i < $min) {
                $obj = $this->db->fetch_object($result);
                $timespent_static = new TimeSpent($this->db);
                if ($timespent_static->fetch($obj->rowid)) {
                    $obj_ret[] = $this->_filterObjectProperties($this->_cleanObjectDatas($timespent_static), $properties);
                }
                $i++;
            }
        } else {
            throw new RestException(503, 'Error when retrieve time spent list : ' . $this->db->lasterror());
        }

        return $obj_ret;
    }

    /**
     * Create time spent object
     *
     * @param   array   $request_data   Request data
     * @return  int     ID of created object
     *
     * @url POST /spent
     */
    public function spent_post($request_data = null)
    {
        if (!DolibarrApiAccess::$user->hasRight('timekeepr', 'write')) {
            throw new RestException(403, "Insufficient rights. Required: timekeepr/saisir");
        }

        // Check mandatory fields
        foreach (self::$FIELDS_SPENT as $field) {
            if (!isset($request_data[$field])) {
                throw new RestException(400, "$field field missing");
            }
        }

        foreach ($request_data as $field => $value) {
            if ($field === 'caller') {
                $this->timespent->context['caller'] = sanitizeVal($request_data['caller'], 'aZ09');
                continue;
            }
            $this->timespent->$field = $this->_checkValForAPI($field, $value, $this->timespent);
        }

        // Required fields validation
        if (empty($this->timespent->fk_element) || empty($this->timespent->elementtype) || empty($this->timespent->element_duration)) {
            throw new RestException(400, "fk_element, elementtype and element_duration are mandatory");
        }

        // Set default values if not provided
        if (empty($this->timespent->fk_user)) {
            $this->timespent->fk_user = DolibarrApiAccess::$user->id;
        }

        if (empty($this->timespent->element_date)) {
            $this->timespent->element_date = dol_now();
        }

        if ($this->timespent->create(DolibarrApiAccess::$user) < 0) {
            throw new RestException(500, "Error creating time spent", array_merge(array($this->timespent->error), $this->timespent->errors));
        }

        return $this->timespent->id;
    }

    /**
     * Update time spent object
     *
     * @param   int     $id             ID of time spent to update
     * @param   array   $request_data   Data
     * @return  Object                  Updated object
     *
     * @url PUT /spent/{id}
     */
    public function spent_put($id, $request_data = null)
    {
        if (!DolibarrApiAccess::$user->hasRight('timekeepr', 'saisir')) {
            throw new RestException(403, "Insufficient rights. Required: timekeepr/saisir");
        }

        $result = $this->timespent->fetch($id);
        if (!$result) {
            throw new RestException(404, 'Time spent not found');
        }

        if (!DolibarrApi::_checkAccessToResource('timespent', $this->timespent->id)) {
            throw new RestException(403, 'Access not allowed for login ' . DolibarrApiAccess::$user->login);
        }

        foreach ($request_data as $field => $value) {
            if ($field == 'id') {
                continue;
            }
            if ($field === 'caller') {
                $this->timespent->context['caller'] = sanitizeVal($request_data['caller'], 'aZ09');
                continue;
            }
            $this->timespent->$field = $this->_checkValForAPI($field, $value, $this->timespent);
        }

        if ($this->timespent->update(DolibarrApiAccess::$user) > 0) {
            return $this->spent_get($id);
        } else {
            throw new RestException(500, $this->timespent->error);
        }
    }

    /**
     * Delete time spent
     *
     * @param   int     $id     Time spent ID
     * @return  array
     *
     * @url DELETE /spent/{id}
     */
    public function spent_delete($id)
    {
        if (!DolibarrApiAccess::$user->hasRight('timekeepr', 'saisir')) {
            throw new RestException(403, "Insufficient rights. Required: timekeepr/saisir");
        }
        
        $result = $this->timespent->fetch($id);
        if (!$result) {
            throw new RestException(404, 'Time spent not found');
        }

        if (!DolibarrApi::_checkAccessToResource('timespent', $this->timespent->id)) {
            throw new RestException(403, 'Access not allowed for login ' . DolibarrApiAccess::$user->login);
        }

        if ($this->timespent->delete(DolibarrApiAccess::$user) <= 0) {
            throw new RestException(500, 'Error when delete time spent : ' . $this->timespent->error);
        }

        return array(
            'success' => array(
                'code' => 200,
                'message' => 'Time spent deleted'
            )
        );
    }

    /**
     * Get time spent summary by element
     *
     * @param   int     $fk_element     ID of element
     * @param   string  $elementtype    Type of element (e.g., 'project', 'task')
     * @return  array                   Summary data
     *
     * @url GET /spent/summary/element/{fk_element}/{elementtype}
     */
    public function spent_summary_by_element($fk_element, $elementtype)
    {
        if (!DolibarrApiAccess::$user->hasRight('timekeepr', 'read')) {
            throw new RestException(403, "Access denied. Required right: timekeepr/read");
        }

        $sql = "SELECT SUM(element_duration) as total_duration, COUNT(*) as total_entries, fk_user";
        $sql .= " FROM " . MAIN_DB_PREFIX . "element_time";
        $sql .= " WHERE fk_element = " . ((int) $fk_element);
        $sql .= " AND elementtype = '" . $this->db->escape($elementtype) . "'";
        $sql .= " GROUP BY fk_user";

        $result = $this->db->query($sql);
        if (!$result) {
            throw new RestException(500, 'Error when retrieving time spent summary: ' . $this->db->lasterror());
        }

        $summary = array();
        while ($obj = $this->db->fetch_object($result)) {
            $summary[] = array(
                'fk_user' => $obj->fk_user,
                'total_duration' => $obj->total_duration,
                'total_entries' => $obj->total_entries
            );
        }

        return array(
            'fk_element' => $fk_element,
            'elementtype' => $elementtype,
            'summary' => $summary
        );
    }

    /**
     * Get time spent by user and period
     *
     * @param   int     $fk_user        ID of user
     * @param   string  $date_start     Start date (YYYY-MM-DD)
     * @param   string  $date_end       End date (YYYY-MM-DD)
     * @return  array                   Time spent data
     *
     * @url GET /spent/user/{fk_user}/period/{date_start}/{date_end}
     */
    public function spent_by_user_period($fk_user, $date_start, $date_end)
    {
        if (!DolibarrApiAccess::$user->hasRight('timekeepr', 'read')) {
            throw new RestException(403, "Access denied. Required right: timekeepr/read");
        }

        $sql = "SELECT t.rowid, t.fk_element, t.elementtype, t.element_date, t.element_duration, t.note";
        $sql .= " FROM " . MAIN_DB_PREFIX . "element_time AS t";
        $sql .= " WHERE t.fk_user = " . ((int) $fk_user);
        $sql .= " AND t.element_date >= '" . $this->db->escape($date_start) . "'";
        $sql .= " AND t.element_date <= '" . $this->db->escape($date_end) . "'";
        $sql .= " ORDER BY t.element_date DESC";

        $result = $this->db->query($sql);
        if (!$result) {
            throw new RestException(500, 'Error when retrieving time spent by user: ' . $this->db->lasterror());
        }

        $timespent = array();
        while ($obj = $this->db->fetch_object($result)) {
            $timespent_static = new TimeSpent($this->db);
            if ($timespent_static->fetch($obj->rowid)) {
                $timespent[] = $this->_cleanObjectDatas($timespent_static);
            }
        }

        return $timespent;
    }

    /**
     * Clean sensitive object data
     *
     * @param   Object  $object     Object to clean
     * @return  Object              Object with cleaned properties
     */
    protected function _cleanObjectDatas($object)
    {
        // Sauvegarder la note si c'est un TimeSpent AVANT le nettoyage parent
        $note = null;
        if ($object instanceof TimeSpent && property_exists($object, 'note')) {
            $note = $object->note;
        }

        $object = parent::_cleanObjectDatas($object);

        // Réassigner la note après le nettoyage parent
        if ($note !== null) {
            $object->note = $note;
        }

        // Champs communs à nettoyer pour TimePlanned et TimeSpent
        $fieldsToRemove = array(
            'barcode_type', 'barcode_type_code', 'barcode_type_label', 'barcode_type_coder',
            'cond_reglement_id', 'cond_reglement', 'fk_delivery_address', 'shipping_method_id',
            'fk_account', 'fk_incoterms', 'label_incoterms', 'location_incoterms',
            'name', 'lastname', 'firstname', 'civility_id', 'mode_reglement_id',
            'country', 'country_id', 'country_code'
        );

        foreach ($fieldsToRemove as $field) {
            if (property_exists($object, $field)) {
                unset($object->$field);
            }
        }

        // Pour les autres objets (non TimeSpent), supprimer la note si elle existe
        if (!($object instanceof TimeSpent) && property_exists($object, 'note')) {
            unset($object->note);
        }

        if (property_exists($object, 'rowid') && empty($object->rowid) && !empty($object->id)) {
            $object->rowid = $object->id;
        }

        return $object;
    }
}
